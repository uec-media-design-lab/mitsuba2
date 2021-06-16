#include <mitsuba/core/properties.h>
#include <mitsuba/core/warp.h>
#include <mitsuba/render/bsdf.h>
#include <mitsuba/render/fresnel.h>
#include <mitsuba/render/ior.h>
#include <mitsuba/render/texture.h>

NAMESPACE_BEGIN(mitsuba);

/**!
.. _bsdf-conductor:

MMAPs (:monosp:`mmaps`)
------------------------------------------------

.. pluginparameters::
 * - base
   - |spectrum|
   - Base color of this bsdf (default: 1.0)

This plugin implements a retro-transmissive interface which transfer the light 
from light source to plane-symmetric position with respect to a mesh has 
this bsdf. 
The main objective of this implementation is improvement of rendering efficiency
in differentiable rendering.

.. code-block:: xml
    :name: lst-mmaps-files

    <bsdf type="mmaps">
        <spectrum name="base" filename="base-color.spd"/>
    </bsdf>

This plugin will not be support *polarized* rendering modes.
 */

template <typename Float>
Vector<Float, 3> retro_transmit(const Vector<Float, 3> &wi, const Normal<Float, 3> &m)
{
    return fmadd(Vector<Float, 3>(m), 2.f * dot(wi, m), -wi);
}

template <typename Float, typename Spectrum>
class MMAPs final : public BSDF<Float, Spectrum> {
public:
    MTS_IMPORT_BASE(BSDF, m_flags, m_components)
    MTS_IMPORT_TYPES(Texture)

    MMAPs(const Properties &props) : Base(props) {
        /*m_flags = BSDFFlags::DeltaReflection | BSDFFlags::FrontSide;
        m_components.push_back(m_flags);*/
        if(!props.has_property("base")) 
            Throw("Should have any base color.");
        m_base = props.texture<Texture>("base", 1.0f);
    }

    std::pair<BSDFSample3f, Spectrum> sample(const BSDFContext &ctx,
                                            const SurfaceInteration3d &si,
                                            Float /* sample1 */,
                                            const Point2f &/*sample2*/,
                                            Mask active) const override {
        MTS_MASKED_FUNCTION(ProfilerPhase::BSDFSample, active);

        Float cos_theta_i = Frame3f::cos_theta(si.wi);
        active &= cos_theta_i > 0.f;

        BSDFSample3f bs = zero<BSDFSample3f>();
        Spectrum value(0.f);
        if (unlikely(none_or<false>(active) || !ctx.is_enabled(BSDFFlags::DeltaReflection))
            return {bs, value};
        
        bs.sampled_component = 0;
        bs.sample_type = +BSDFFlags::DeltaReflection;
        bs.wo = retro_transmit(si.wi, si.n);
        bs.eta = 1.f;   // Index of refraction
        bs.pdf = 1.f;   // Posibility distribution function

        UnpolarizedSpectrum retro_transmittance = m_retro_transmittance->eval(si, active);
        UnpolarizedSpectrum base = m_base->eval(si, active);

        if constexpr (is_polarized_v<Spectrum>) {
            /**
             * NOTE:
             * This brdf is implemented for improving inverse rendering efficiency in optimizing `InFloasion` optical system.
             * The optimization won't performed with `polarized mode`, so this function never support it.
             **/

            // Vector3f wi_hat = ctx.mode == TransportMode::Radiance ? bs.wo : si.wi,
            //          wo_hat = ctx.mode == TransportMode::Radiance ? si.wi : bs.wo;

            // value = mueller::specular_reflection(UnpolarizedSpectrum(Frame3f::cos_theta(wi_hat)), base);

            // value = muller::reverse(value);

            // Vector3f n(0, 0, 1);
            // Vector3f s_axis_in = normalize(cross(n, -wi_hat)),
            //          p_axis_in = normalize(cross(-wi_hat, s_axis_in)),
            //          s_axis_out = normalize(cross(n, wo_hat)),
            //          p_axis_out = normalize(cross(wo_hat, s_axis_out));
                
            // value = mueller::rotate_mueller_basis(value, 
            //                                       -wi_hat, p_axis_in, mueller::stokes_basis(-wi_hat),
            //                                       wo_hat, p_axis_out, mueller::stokes_basis(wo_hat));
            // value *= mueller::absorber(retro_transmittance);
        } else {
            value = retro_transmittance * base;
        }

        return { bs, value & active };
    }

    Spectrum eval(const BSDFContext & /*ctx*/, const SurfaceInteraction & /*si*/,
                const Vector3f & /*wo*/, Mask /*active*/ ) const {
        return 0.f;
    }

    Float pdf(const BSDFContext & /*ctx*/, const SurfaceInteraction3f &/*si*/,
              const Vector3f & /*wo*/, Mask /*active*/ ) const override {
        return 0.f;
    }

    void traverse(TraversalCallback *callback) override {
        callback->put_object("retro_transmittance", m_retro_transmittance.get());
        callback->put_object("base", m_base.get());
    }

    std::string to_string() const override {
        std::ostringstream oss;
        oss << "MMAPsBSDF[" << std::endl
            << " base = " << string::indent(m_eta) << "," << std::endl
            << " k = " << string::indent(m_k) << "," << std::endl
            << "]";
        return oss.str();
    }

    MTS_DECLARE_CLASS()
private:
    ref<Texture> m_base;
    ref<Texture> m_retro_transmittance;
};

MTS_IMPLEMENT_CLASS_VARIANT(MMAPs, BSDF);
MTS_EXPORT_PLUGIN(MMAPs, "MMAPs")
NAMESPACE_END(mitsuba);